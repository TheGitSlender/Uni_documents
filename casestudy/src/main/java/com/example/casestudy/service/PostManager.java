package com.example.casestudy.service;

import com.example.casestudy.model.Post;

import java.util.List;

public interface PostManager {

    Post addPost(Post post);
    List<Post> getAllPosts();
    List<Post> getPostsByTagNames(List<String> tagNames);
    Post getPostById(Long id);
    Post updatePost(Long id, Post post);
    void deletePost(Long id);
}
