package com.example.casestudy.service;

import com.example.casestudy.model.Comment;
import com.example.casestudy.model.Post;
import com.example.casestudy.repository.CommentRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class CommentService {

    @Autowired
    private CommentRepository commentRepository;

    public Comment addComment(Comment comment) {
        return commentRepository.save(comment);
    }

    public Comment getCommentById(Long id) {
        return commentRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Comment not found with id: " + id));
    }

    public Comment updateComment(Long id, String content) {
        Comment comment = getCommentById(id);
        comment.setContent(content);
        return commentRepository.save(comment);
    }

    @Transactional
    public void deleteComment(Long id) {
        Comment comment = getCommentById(id);
        Post post = comment.getPost();
        if (post != null) {
            post.getComments().remove(comment);
            comment.setPost(null);
        }
        commentRepository.delete(comment);
    }
}
