package io.casehub.platform.bootstrap;

import io.casehub.platform.bootstrap.spi.ClasspathYamlRegistrar;
import io.quarkus.runtime.StartupEvent;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.enterprise.event.Observes;
import jakarta.enterprise.inject.Instance;
import jakarta.inject.Inject;
import org.jboss.logging.Logger;
import org.yaml.snakeyaml.Yaml;

import java.io.IOException;
import java.io.InputStream;
import java.net.URL;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.Enumeration;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

@ApplicationScoped
public class ClasspathBootstrap {

    private static final Logger LOG = Logger.getLogger(ClasspathBootstrap.class);
    private static final String APP_MANIFEST_PATH = "META-INF/app.yaml";

    @Inject
    Instance<ClasspathYamlRegistrar> registrars;

    private AppManifest appManifest;

    void onStart(@Observes StartupEvent event) {
        appManifest = loadAppManifest();
        if (appManifest != null) {
            LOG.infof("CaseHub app: %s v%s", appManifest.name(), appManifest.version());
        }

        List<ClasspathYamlRegistrar> sorted = new ArrayList<>();
        registrars.forEach(sorted::add);
        sorted.sort(Comparator.comparingInt(ClasspathYamlRegistrar::priority));

        if (sorted.isEmpty()) {
            LOG.debug("No ClasspathYamlRegistrar beans found — skipping bootstrap scan");
            return;
        }

        Set<String> handledSections = new HashSet<>();
        int totalFiles = 0;

        for (ClasspathYamlRegistrar registrar : sorted) {
            handledSections.add(registrar.sectionKey());
            int count = scanAndRegister(registrar);
            totalFiles += count;
            if (count > 0) {
                LOG.infof("  [%s] priority=%d, registered %d file(s)", registrar.sectionKey(), registrar.priority(), count);
            }
        }

        LOG.infof("Bootstrap complete: %d section(s) handled, %d file(s) registered", handledSections.size(), totalFiles);
    }

    public AppManifest getAppManifest() {
        return appManifest;
    }

    int scanAndRegister(ClasspathYamlRegistrar registrar) {
        int count = 0;
        ClassLoader cl = Thread.currentThread().getContextClassLoader();

        for (String path : registrar.classpathPaths()) {
            String normalised = path.endsWith("/") ? path : path + "/";
            try {
                Enumeration<URL> resources = cl.getResources(normalised);
                while (resources.hasMoreElements()) {
                    URL dirUrl = resources.nextElement();
                    List<String> yamlFiles = discoverYamlFiles(dirUrl, normalised, cl);
                    for (String resourcePath : yamlFiles) {
                        try (InputStream is = cl.getResourceAsStream(resourcePath)) {
                            if (is != null) {
                                registrar.register(resourcePath, is);
                                count++;
                            }
                        }
                    }
                }
            } catch (IOException e) {
                LOG.warnf("Failed to scan classpath path '%s' for section '%s': %s", path, registrar.sectionKey(), e.getMessage());
            }
        }
        return count;
    }

    List<String> discoverYamlFiles(URL dirUrl, String basePath, ClassLoader cl) throws IOException {
        List<String> result   = new ArrayList<>();
        String       protocol = dirUrl.getProtocol();
        if ("file".equals(protocol)) {
            java.io.File dir = new java.io.File(dirUrl.getPath());
            collectYamlFiles(dir, basePath, result);
        } else if ("jar".equals(protocol)) {
            java.net.JarURLConnection jarConn = (java.net.JarURLConnection) dirUrl.openConnection();
            try (java.util.jar.JarFile jarFile = jarConn.getJarFile()) {
                java.util.Enumeration<java.util.jar.JarEntry> entries = jarFile.entries();
                while (entries.hasMoreElements()) {
                    java.util.jar.JarEntry entry = entries.nextElement();
                    String                 name  = entry.getName();
                    if (!entry.isDirectory() && name.startsWith(basePath) && isYamlFile(name)) {
                        result.add(name);
                    }
                }
            }
        } else {
            LOG.debugf("Unsupported classpath URL protocol '%s' for path '%s' — skipping", protocol, basePath);
        }
        return result;
    }

    private void collectYamlFiles(java.io.File dir, String basePath, List<String> result) {
        java.io.File[] files = dir.listFiles();
        if (files == null) {
            return;
        }
        for (java.io.File file : files) {
            if (file.isDirectory()) {
                collectYamlFiles(file, basePath + file.getName() + "/", result);
            } else if (isYamlFile(file.getName())) {
                result.add(basePath + file.getName());
            }
        }
    }

    private boolean isYamlFile(String name) {
        return name.endsWith(".yaml") || name.endsWith(".yml");
    }

    @SuppressWarnings("unchecked")
    AppManifest loadAppManifest() {
        ClassLoader cl = Thread.currentThread().getContextClassLoader();
        try (InputStream is = cl.getResourceAsStream(APP_MANIFEST_PATH)) {
            if (is == null) {
                LOG.debug("No META-INF/app.yaml found — skipping manifest");
                return null;
            }
            Yaml yaml = new Yaml();
            Map<String, Object> root = yaml.load(is);
            if (root == null || !root.containsKey("app")) {
                LOG.warn("META-INF/app.yaml found but missing 'app' section");
                return null;
            }
            Map<String, Object> app = (Map<String, Object>) root.get("app");
            String name = (String) app.get("name");
            String version = app.get("version") != null ? app.get("version").toString() : null;

            List<String> required = List.of();
            List<String> optional = List.of();
            if (app.containsKey("modules")) {
                Map<String, Object> modules = (Map<String, Object>) app.get("modules");
                if (modules != null) {
                    if (modules.containsKey("required")) {
                        required = toStringList(modules.get("required"));
                    }
                    if (modules.containsKey("optional")) {
                        optional = toStringList(modules.get("optional"));
                    }
                }
            }
            return new AppManifest(name, version, required, optional);
        } catch (IOException e) {
            LOG.warnf("Failed to read META-INF/app.yaml: %s", e.getMessage());
            return null;
        }
    }

    @SuppressWarnings("unchecked")
    private List<String> toStringList(Object value) {
        if (value instanceof List<?> list) {
            return list.stream().map(Object::toString).toList();
        }
        return List.of();
    }
}
