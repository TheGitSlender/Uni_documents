package com.example.casestudy.controller;

import com.example.casestudy.model.Post;
import com.example.casestudy.model.ReactionType;
import com.example.casestudy.model.User;
import com.example.casestudy.service.PostService;
import com.example.casestudy.service.ReactionService;
import com.example.casestudy.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

import java.security.Principal;

@Controller
@RequestMapping("/posts/{id}/react")
public class ReactionController {

    @Autowired
    private ReactionService reactionService;

    @Autowired
    private PostService postService;

    @Autowired
    private UserService userService;

    @PostMapping
    public String react(@PathVariable Long id,
                        @RequestParam ReactionType type,
                        Principal principal,
                        RedirectAttributes redirectAttributes) {
        try {
            Post post = postService.getPostById(id);
            User user = userService.getUserByUsername(principal.getName());
            reactionService.react(post, user, type);
        } catch (Exception e) {
            redirectAttributes.addFlashAttribute("errorMessage", "Could not save reaction.");
        }
        return "redirect:/posts/" + id;
    }
}
