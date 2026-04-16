package com.example.casestudy.controller;

import com.example.casestudy.service.CommentService;
import com.example.casestudy.service.PostService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

@Controller
@RequestMapping("/admin")
public class AdminController {

    @Autowired
    private PostService postService;

    @Autowired
    private CommentService commentService;

    @GetMapping({"", "/"})
    public String dashboard(Model model) {
        model.addAttribute("posts", postService.getAllPosts());
        return "admin/dashboard";
    }

    @PostMapping("/posts/{id}/delete")
    public String deletePost(@PathVariable Long id, RedirectAttributes redirectAttributes) {
        try {
            postService.deletePost(id);
            redirectAttributes.addFlashAttribute("successMessage", "Post deleted.");
        } catch (Exception e) {
            redirectAttributes.addFlashAttribute("errorMessage", "Error deleting post: " + e.getMessage());
        }
        return "redirect:/admin";
    }

    @PostMapping("/posts/{postId}/comments/{id}/delete")
    public String deleteComment(@PathVariable Long postId,
                                @PathVariable Long id,
                                RedirectAttributes redirectAttributes) {
        try {
            commentService.deleteComment(id);
            redirectAttributes.addFlashAttribute("successMessage", "Comment deleted.");
        } catch (Exception e) {
            redirectAttributes.addFlashAttribute("errorMessage", "Error deleting comment: " + e.getMessage());
        }
        return "redirect:/admin";
    }
}
