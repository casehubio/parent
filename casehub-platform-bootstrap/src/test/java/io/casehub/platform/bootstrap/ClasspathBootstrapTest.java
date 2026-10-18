package io.casehub.platform.bootstrap;

import io.casehub.platform.bootstrap.spi.ClasspathYamlRegistrar;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;

import static org.assertj.core.api.Assertions.assertThat;

class ClasspathBootstrapTest {

    @Test
    void scanAndRegisterFindsYamlFiles(@TempDir Path tempDir) throws IOException {
        Path casehubDir = tempDir.resolve("casehub");
        Files.createDirectories(casehubDir);
        Files.writeString(casehubDir.resolve("test-case.yaml"), "name: test-case\n");
        Files.writeString(casehubDir.resolve("another.yml"), "name: another\n");
        Files.writeString(casehubDir.resolve("not-yaml.txt"), "ignored\n");

        ClasspathBootstrap bootstrap = new ClasspathBootstrap();

        java.net.URL dirUrl = casehubDir.toUri().toURL();
        List<String> discovered = bootstrap.discoverYamlFiles(dirUrl, "casehub/", Thread.currentThread().getContextClassLoader());

        assertThat(discovered)
                .hasSize(2)
                .anyMatch(p -> p.endsWith("test-case.yaml"))
                .anyMatch(p -> p.endsWith("another.yml"));
    }

    @Test
    void discoverYamlFilesScansSubdirectories(@TempDir Path tempDir) throws IOException {
        Path casesDir = tempDir.resolve("cases");
        Path subDir = casesDir.resolve("sub");
        Files.createDirectories(subDir);
        Files.writeString(casesDir.resolve("top.yaml"), "name: top\n");
        Files.writeString(subDir.resolve("nested.yaml"), "name: nested\n");

        ClasspathBootstrap bootstrap = new ClasspathBootstrap();
        java.net.URL dirUrl = casesDir.toUri().toURL();
        List<String> discovered = bootstrap.discoverYamlFiles(dirUrl, "cases/", Thread.currentThread().getContextClassLoader());

        assertThat(discovered)
                .hasSize(2)
                .anyMatch(p -> p.equals("cases/top.yaml"))
                .anyMatch(p -> p.equals("cases/sub/nested.yaml"));
    }

    @Test
    void loadAppManifestParsesValidYaml() {
        ClasspathBootstrap bootstrap = new ClasspathBootstrap();
        AppManifest manifest = bootstrap.loadAppManifest();
        assertThat(manifest).isNotNull();
        assertThat(manifest.name()).isEqualTo("test-app");
        assertThat(manifest.version()).isEqualTo("1.0");
        assertThat(manifest.requiredModules()).containsExactly("casehub-engine-runtime");
        assertThat(manifest.optionalModules()).containsExactly("casehub-engine-ai");
    }

    @Test
    void appManifestDefensiveCopy() {
        List<String> required = new ArrayList<>(List.of("a", "b"));
        List<String> optional = new ArrayList<>(List.of("c"));
        AppManifest manifest = new AppManifest("test", "1.0", required, optional);

        required.add("mutated");
        assertThat(manifest.requiredModules()).containsExactly("a", "b");
        assertThat(manifest.optionalModules()).containsExactly("c");
    }

    @Test
    void appManifestNullLists() {
        AppManifest manifest = new AppManifest("test", "1.0", null, null);
        assertThat(manifest.requiredModules()).isEmpty();
        assertThat(manifest.optionalModules()).isEmpty();
    }

    static class RecordingRegistrar implements ClasspathYamlRegistrar {
        final String sectionKey;
        final Set<String> paths;
        final int priority;
        final List<String> registeredPaths = new ArrayList<>();

        RecordingRegistrar(String sectionKey, Set<String> paths, int priority) {
            this.sectionKey = sectionKey;
            this.paths = paths;
            this.priority = priority;
        }

        @Override public String sectionKey() { return sectionKey; }
        @Override public Set<String> classpathPaths() { return paths; }
        @Override public int priority() { return priority; }
        @Override public void register(String resourcePath, InputStream content) {
            registeredPaths.add(resourcePath);
        }
    }
}
