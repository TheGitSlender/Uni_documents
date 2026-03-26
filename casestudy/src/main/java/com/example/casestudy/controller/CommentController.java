package com.example.casestudy.controller;

import com.example.casestudy.model.Comment;
import com.example.casestudy.model.Post;
import com.example.casestudy.model.User;
import com.example.casestudy.service.CommentService;
import com.example.casestudy.service.PostManager;
import com.example.casestudy.service.UserService;
import org.springframework.security.core.Authentication;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

import java.security.Principal;

@Controller
public class CommentController {

    private final CommentService commentService;
    private final PostManager postManager;
    private final UserService userService;

    public CommentController(CommentService commentService, PostManager postManager, UserService userService) {
        this.commentService = commentService;
        this.postManager = postManager;
        this.userService = userService;
    }

    @PostMapping("/posts/{postId}/comments")
    public String addComment(@PathVariable Long postId,
                             @RequestParam String content,
                             Principal principal,
                             RedirectAttributes redirectAttributes) {
        try {
            Post post = postManager.getPostById(postId);
            User author = userService.getUserByUsername(principal.getName());
            commentService.addComment(new Comment(content, post, author));
            redirectAttributes.addFlashAttribute("successMessage", "Comment added!");
        } catch (Exception e) {
            redirectAttributes.addFlashAttribute("errorMessage", "Error adding comment: " + e.getMessage());
        }
        return "redirect:/posts/" + postId;
    }

    @PostMapping("/posts/{postId}/comments/{id}/update")
    public String updateComment(@PathVariable Long postId,
                                @PathVariable Long id,
                                @RequestParam String content,
                                Principal principal,
                                RedirectAttributes redirectAttributes) {
        try {
            Comment comment = commentService.getCommentById(id);
            if (!isOwnerOrAdmin(comment, principal)) {
                redirectAttributes.addFlashAttribute("errorMessage", "You can only edit your own comments.");
                return "redirect:/posts/" + postId;
            }
            commentService.updateComment(id, content);
            redirectAttributes.addFlashAttribute("successMessage", "Comment updated!");
        } catch (Exception e) {
            redirectAttributes.addFlashAttribute("errorMessage", "Error updating comment: " + e.getMessage());
        }
        return "redirect:/posts/" + postId;
    }

    @PostMapping("/posts/{postId}/comments/{id}/delete")
    public String deleteComment(@PathVariable Long postId,
                                @PathVariable Long id,
                                Principal principal,
                                RedirectAttributes redirectAttributes) {
        try {
            Comment comment = commentService.getCommentById(id);
            if (!isOwnerOrAdmin(comment, principal)) {
                redirectAttributes.addFlashAttribute("errorMessage", "You can only delete your own comments.");
                return "redirect:/posts/" + postId;
            }
            commentService.deleteComment(id);
            redirectAttributes.addFlashAttribute("successMessage", "Comment deleted!");
        } catch (Exception e) {
            redirectAttributes.addFlashAttribute("errorMessage", "Error deleting comment: " + e.getMessage());
        }
        return "redirect:/posts/" + postId;
    }

    private boolean isOwnerOrAdmin(Comment comment, Principal principal) {
        if (principal == null) return false;
        Authentication auth = (Authentication) principal;
        boolean isAdmin = auth.getAuthorities().stream()
                .anyMatch(a -> a.getAuthority().equals("ROLE_ADMIN"));
        return isAdmin || principal.getName().equals(comment.getAuthorName());
    }
}
