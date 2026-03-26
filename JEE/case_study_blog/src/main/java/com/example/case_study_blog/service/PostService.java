package com.example.case_study_blog.service;

import com.example.case_study_blog.entity.Post;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

@Service
public class PostService {

    private final List<Post> posts = new ArrayList<>();
    private Long nextId = 1L;

    public List<Post> getAllPosts() {
        return posts;
    }

    public Post createPost(Post post) {
        post.setId(nextId++);
        posts.add(post);
        return post;
    }

    public Post getPostById(Long id) {
        return posts.stream()
                .filter(p -> p.getId().equals(id))
                .findFirst()
                .orElse(null);
    }
}