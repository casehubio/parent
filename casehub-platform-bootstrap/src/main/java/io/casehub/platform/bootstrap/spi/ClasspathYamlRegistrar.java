package io.casehub.platform.bootstrap.spi;

import java.io.InputStream;
import java.util.Set;

public interface ClasspathYamlRegistrar {

    String sectionKey();

    Set<String> classpathPaths();

    int priority();

    void register(String resourcePath, InputStream content);
}
