package com.example.casestudy.service;

import com.example.casestudy.model.Comment;
import com.example.casestudy.model.Post;

import java.util.List;

public interface CommentService {
    Comment addComment(Comment comment);
    List<Comment> getCommentsByPost(Post post);
    Comment getCommentById(Long id);
    Comment updateComment(Long id, String content);
    void deleteComment(Long id);
}
