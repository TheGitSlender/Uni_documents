package com.example.casestudy.util;

import org.springframework.security.core.Authentication;

import java.security.Principal;

public class AuthUtils {

    private AuthUtils() {}

    public static boolean isOwner(String authorName, Principal principal) {
        return principal != null && principal.getName().equals(authorName);
    }

    public static boolean isOwnerOrAdmin(String authorName, Principal principal) {
        if (principal == null) return false;
        Authentication auth = (Authentication) principal;
        boolean isAdmin = auth.getAuthorities().stream()
                .anyMatch(a -> a.getAuthority().equals("ROLE_ADMIN"));
        return isAdmin || principal.getName().equals(authorName);
    }
}
