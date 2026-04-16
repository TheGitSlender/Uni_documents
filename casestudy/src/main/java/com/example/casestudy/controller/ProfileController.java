package com.example.casestudy.controller;

import com.example.casestudy.model.Profile;
import com.example.casestudy.model.User;
import com.example.casestudy.repository.ProfileRepository;
import com.example.casestudy.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

import java.security.Principal;

@Controller
@RequestMapping("/profile")
public class ProfileController {

    @Autowired
    private ProfileRepository profileRepository;

    @Autowired
    private UserService userService;

    @GetMapping
    public String viewProfile(Model model, Principal principal) {
        User user = userService.getUserByUsername(principal.getName());
        Profile profile = profileRepository.findByUser(user)
                .orElseGet(() -> profileRepository.save(new Profile(null, null, user)));
        model.addAttribute("profile", profile);
        return "profile/view";
    }

    @PostMapping
    public String updateBio(@RequestParam(required = false) String bio,
                            Principal principal,
                            RedirectAttributes redirectAttributes) {
        try {
            User user = userService.getUserByUsername(principal.getName());
            Profile profile = profileRepository.findByUser(user)
                    .orElseGet(() -> new Profile(null, null, user));
            profile.setBio(bio);
            profileRepository.save(profile);
            redirectAttributes.addFlashAttribute("successMessage", "Profile updated!");
        } catch (Exception e) {
            redirectAttributes.addFlashAttribute("errorMessage", "Error updating profile: " + e.getMessage());
        }
        return "redirect:/profile";
    }
}
