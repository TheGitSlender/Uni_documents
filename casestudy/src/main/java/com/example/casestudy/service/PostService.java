package com.example.casestudy.service;

import com.example.casestudy.model.Post;
import com.example.casestudy.repository.PostRepository;
import com.example.casestudy.repository.TagRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class PostService {

    @Autowired
    private PostRepository postRepository;

    @Autowired
    private TagRepository tagRepository;

    public Post addPost(Post post) {
        return postRepository.save(post);
    }

    public List<Post> getAllPosts() {
        return postRepository.findAll();
    }

    public List<Post> getPostsByTagNames(List<String> tagNames) {
        return postRepository.findByAllTagNames(tagNames, tagNames.size());
    }

    public Post getPostById(Long id) {
        return postRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Post not found with id: " + id));
    }

    public Post updatePost(Post post) {
        return postRepository.save(post);
    }

    @Transactional
    public void deletePost(Long id) {
        Post post = postRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Post not found with id: " + id));
        if (post.getAuthor() != null) {
            post.getAuthor().getPosts().remove(post);
            post.setAuthor(null);
        }
        post.getTags().clear();
        postRepository.delete(post);
        tagRepository.deleteAll(tagRepository.findOrphanedTags());
    }
}
