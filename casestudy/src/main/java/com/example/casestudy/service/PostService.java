package com.example.casestudy.service;

import com.example.casestudy.model.Post;
import com.example.casestudy.repository.PostRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class PostService implements PostManager {

    private final PostRepository postRepository;

    public PostService(PostRepository postRepository) {
        this.postRepository = postRepository;
    }

    @Override
    public Post addPost(Post post) {
        return postRepository.save(post);
    }

    @Override
    public List<Post> getAllPosts() {
        return postRepository.findAll();
    }

    @Override
    public List<Post> getPostsByTagNames(List<String> tagNames) {
        if (tagNames == null || tagNames.isEmpty()) return postRepository.findAll();
        return postRepository.findByAllTagNames(tagNames, tagNames.size());
    }

    @Override
    public Post getPostById(Long id) {
        return postRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Post not found with id: " + id));
    }

    @Override
    public Post updatePost(Long id, Post post) {
        Post existing = postRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Post not found with id: " + id));
        existing.setContent(post.getContent());
        existing.setAuthor(post.getAuthor());
        existing.setTags(post.getTags());
        return postRepository.save(existing);
    }

    @Override
    @Transactional
    public void deletePost(Long id) {
        Post post = postRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Post not found with id: " + id));
        // Unlink from author's collection so Hibernate doesn't re-persist on flush
        if (post.getAuthor() != null) {
            post.getAuthor().getPosts().remove(post);
            post.setAuthor(null);
        }
        // Clear tags join table
        post.getTags().clear();
        postRepository.delete(post);
    }
}