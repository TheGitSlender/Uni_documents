package com.example.casestudy.controller;

import com.example.casestudy.model.Post;
import com.example.casestudy.model.Tag;
import com.example.casestudy.model.User;
import com.example.casestudy.repository.TagRepository;
import com.example.casestudy.service.PostManager;
import com.example.casestudy.service.UserService;
import org.springframework.security.core.Authentication;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

import java.security.Principal;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

@Controller
@RequestMapping("/posts")
public class PostController {

    private final PostManager postManager;
    private final UserService userService;
    private final TagRepository tagRepository;

    public PostController(PostManager postManager, UserService userService, TagRepository tagRepository) {
        this.postManager = postManager;
        this.userService = userService;
        this.tagRepository = tagRepository;
    }

    @GetMapping({"", "/"})
    public String listPosts(@RequestParam(required = false) List<String> tags, Model model) {
        List<String> activeTags = (tags != null) ? tags : List.of();
        List<Post> posts = activeTags.isEmpty()
                ? postManager.getAllPosts()
                : postManager.getPostsByTagNames(activeTags);
        model.addAttribute("posts", posts);
        model.addAttribute("allTags", tagRepository.findAll());
        model.addAttribute("activeTags", activeTags);
        return "posts/list";
    }

    @GetMapping("/{id}")
    public String viewPost(@PathVariable Long id, Model model) {
        model.addAttribute("post", postManager.getPostById(id));
        return "posts/view";
    }

    @GetMapping("/new")
    public String showCreatePostForm(Model model) {
        model.addAttribute("post", new Post());
        model.addAttribute("allTags", tagRepository.findAll());
        return "posts/form";
    }

    @PostMapping
    public String createPost(@ModelAttribute Post post,
                             @RequestParam(required = false) String tagNames,
                             Principal principal,
                             RedirectAttributes redirectAttributes) {
        try {
            User author = userService.getUserByUsername(principal.getName());
            post.setAuthor(author);
            post.setTags(resolveTagNames(tagNames));
            postManager.addPost(post);
            redirectAttributes.addFlashAttribute("successMessage", "Post published!");
            return "redirect:/posts";
        } catch (Exception e) {
            redirectAttributes.addFlashAttribute("errorMessage", "Error creating post: " + e.getMessage());
            return "redirect:/posts/new";
        }
    }

    @GetMapping("/edit/{id}")
    public String showEditPostForm(@PathVariable Long id, Model model, Principal principal, RedirectAttributes redirectAttributes) {
        try {
            Post post = postManager.getPostById(id);
            if (!isOwnerOrAdmin(post, principal)) {
                redirectAttributes.addFlashAttribute("errorMessage", "You can only edit your own posts.");
                return "redirect:/posts/" + id;
            }
            model.addAttribute("post", post);
            model.addAttribute("allTags", tagRepository.findAll());
            model.addAttribute("isEdit", true);
            return "posts/form";
        } catch (RuntimeException e) {
            redirectAttributes.addFlashAttribute("errorMessage", "Post not found!");
            return "redirect:/posts";
        }
    }

    @PostMapping("/update/{id}")
    public String updatePost(@PathVariable Long id,
                             @ModelAttribute Post post,
                             @RequestParam(required = false) String tagNames,
                             Principal principal,
                             RedirectAttributes redirectAttributes) {
        try {
            Post existing = postManager.getPostById(id);
            if (!isOwnerOrAdmin(existing, principal)) {
                redirectAttributes.addFlashAttribute("errorMessage", "You can only edit your own posts.");
                return "redirect:/posts/" + id;
            }
            post.setAuthor(existing.getAuthor());
            post.setTags(resolveTagNames(tagNames));
            postManager.updatePost(id, post);
            redirectAttributes.addFlashAttribute("successMessage", "Post updated!");
            return "redirect:/posts";
        } catch (Exception e) {
            redirectAttributes.addFlashAttribute("errorMessage", "Error updating post: " + e.getMessage());
            return "redirect:/posts/edit/" + id;
        }
    }

    @PostMapping("/delete/{id}")
    public String deletePost(@PathVariable Long id, Principal principal, RedirectAttributes redirectAttributes) {
        try {
            Post post = postManager.getPostById(id);
            if (!isOwnerOrAdmin(post, principal)) {
                redirectAttributes.addFlashAttribute("errorMessage", "You can only delete your own posts.");
                return "redirect:/posts/" + id;
            }
            postManager.deletePost(id);
            redirectAttributes.addFlashAttribute("successMessage", "Post deleted!");
        } catch (RuntimeException e) {
            redirectAttributes.addFlashAttribute("errorMessage", "Error deleting post: " + e.getMessage());
        }
        return "redirect:/posts";
    }

    private Set<Tag> resolveTagNames(String tagNames) {
        if (tagNames == null || tagNames.isBlank()) return new HashSet<>();
        return Arrays.stream(tagNames.split(","))
                .map(String::trim)
                .filter(s -> !s.isEmpty())
                .map(name -> tagRepository.findByName(name)
                        .orElseGet(() -> tagRepository.save(new Tag(name))))
                .collect(Collectors.toSet());
    }

    private boolean isOwnerOrAdmin(Post post, Principal principal) {
        if (principal == null) return false;
        String username = principal.getName();
        Authentication auth = (Authentication) principal;
        boolean isAdmin = auth.getAuthorities().stream()
                .anyMatch(a -> a.getAuthority().equals("ROLE_ADMIN"));
        return isAdmin || username.equals(post.getAuthorName());
    }
}
