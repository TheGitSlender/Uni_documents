package com.example.casestudy.controller;

import com.example.casestudy.model.Article;
import com.example.casestudy.model.Post;
import com.example.casestudy.model.ReactionType;
import com.example.casestudy.model.Tag;
import com.example.casestudy.model.User;
import com.example.casestudy.model.VideoPost;
import com.example.casestudy.repository.TagRepository;
import com.example.casestudy.service.PostService;
import com.example.casestudy.service.ReactionService;
import com.example.casestudy.service.UserService;
import com.example.casestudy.util.AuthUtils;
import org.springframework.beans.factory.annotation.Autowired;
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

    @Autowired
    private PostService postService;

    @Autowired
    private UserService userService;

    @Autowired
    private TagRepository tagRepository;

    @Autowired
    private ReactionService reactionService;

    @GetMapping({"", "/"})
    public String listPosts(@RequestParam(required = false) List<String> tags, Model model) {
        List<String> activeTags = (tags != null) ? tags : List.of();
        List<Post> posts = activeTags.isEmpty()
                ? postService.getAllPosts()
                : postService.getPostsByTagNames(activeTags);
        model.addAttribute("posts", posts);
        model.addAttribute("allTags", tagRepository.findAll());
        model.addAttribute("activeTags", activeTags);
        return "posts/list";
    }

    @GetMapping("/{id}")
    public String viewPost(@PathVariable Long id, Model model, Principal principal) {
        Post post = postService.getPostById(id);
        model.addAttribute("post", post);
        model.addAttribute("reactionCounts", reactionService.getReactionCounts(post));
        model.addAttribute("reactionTypes", ReactionType.values());
        if (principal != null) {
            User user = userService.getUserByUsername(principal.getName());
            model.addAttribute("userReaction", reactionService.getUserReactionType(post, user).orElse(null));
        }
        return "posts/view";
    }

    @GetMapping("/new")
    public String showCreatePostForm(Model model) {
        model.addAttribute("post", new Article());
        model.addAttribute("isEdit", false);
        model.addAttribute("allTags", tagRepository.findAll());
        return "posts/form";
    }

    @PostMapping
    public String createPost(@RequestParam(required = false) String content,
                             @RequestParam(required = false) String url,
                             @RequestParam(defaultValue = "article") String type,
                             @RequestParam(required = false) String tagNames,
                             Principal principal,
                             RedirectAttributes redirectAttributes) {
        try {
            User author = userService.getUserByUsername(principal.getName());
            Post post;
            if ("video".equals(type)) {
                if (url == null || url.isBlank()) throw new RuntimeException("URL is required for video posts.");
                post = new VideoPost(url);
            } else {
                if (content == null || content.isBlank()) throw new RuntimeException("Content is required.");
                post = new Article(content);
            }
            post.setAuthor(author);
            post.setTags(resolveTagNames(tagNames));
            postService.addPost(post);
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
            Post post = postService.getPostById(id);
            if (!AuthUtils.isOwner(post.getAuthorName(), principal)) {
                redirectAttributes.addFlashAttribute("errorMessage", "You can only edit your own posts.");
                return "redirect:/posts/" + id;
            }
            model.addAttribute("post", post);
            model.addAttribute("allTags", tagRepository.findAll());
            model.addAttribute("isEdit", true);
            model.addAttribute("postType", post instanceof VideoPost ? "video" : "article");
            return "posts/form";
        } catch (RuntimeException e) {
            redirectAttributes.addFlashAttribute("errorMessage", "Post not found!");
            return "redirect:/posts";
        }
    }

    @PostMapping("/update/{id}")
    public String updatePost(@PathVariable Long id,
                             @RequestParam(required = false) String content,
                             @RequestParam(required = false) String url,
                             @RequestParam(required = false) String tagNames,
                             Principal principal,
                             RedirectAttributes redirectAttributes) {
        try {
            Post existing = postService.getPostById(id);
            if (!AuthUtils.isOwner(existing.getAuthorName(), principal)) {
                redirectAttributes.addFlashAttribute("errorMessage", "You can only edit your own posts.");
                return "redirect:/posts/" + id;
            }
            if (existing instanceof Article a && content != null && !content.isBlank()) {
                a.setContent(content);
            } else if (existing instanceof VideoPost vp && url != null && !url.isBlank()) {
                vp.setUrl(url);
            }
            existing.setTags(resolveTagNames(tagNames));
            postService.updatePost(existing);
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
            Post post = postService.getPostById(id);
            if (!AuthUtils.isOwnerOrAdmin(post.getAuthorName(), principal)) {
                redirectAttributes.addFlashAttribute("errorMessage", "You can only delete your own posts.");
                return "redirect:/posts/" + id;
            }
            postService.deletePost(id);
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
}
