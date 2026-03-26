package com.example.casestudy.controller;

import com.example.casestudy.model.Post;
import com.example.casestudy.service.PostManager;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/posts")
public class PostRestController {

    private final PostManager postManager;

    public PostRestController(PostManager postManager) {
        this.postManager = postManager;
    }

    @GetMapping
    public List<Post> getAllPosts() {
        return postManager.getAllPosts();
    }

    @GetMapping("/{id}")
    public Post getPostById(@PathVariable Long id) {
        return postManager.getPostById(id);
    }

    @PostMapping
    public Post createPost(@RequestBody Post post) {
        return postManager.addPost(post);
    }

    @PutMapping("/{id}")
    public Post updatePost(@PathVariable Long id, @RequestBody Post post) {
        return postManager.updatePost(id, post);
    }

    @DeleteMapping("/{id}")
    public void deletePost(@PathVariable Long id) {
        postManager.deletePost(id);
    }
}
