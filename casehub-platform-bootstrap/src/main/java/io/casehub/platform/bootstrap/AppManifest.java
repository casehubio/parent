package io.casehub.platform.bootstrap;

import java.util.List;

public record AppManifest(
        String name,
        String version,
        List<String> requiredModules,
        List<String> optionalModules) {

    public AppManifest {
        requiredModules = requiredModules != null ? List.copyOf(requiredModules) : List.of();
        optionalModules = optionalModules != null ? List.copyOf(optionalModules) : List.of();
    }
}
