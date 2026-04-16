package com.example.casestudy.repository;

import com.example.casestudy.model.Post;
import com.example.casestudy.model.Reaction;
import com.example.casestudy.model.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface ReactionRepository extends JpaRepository<Reaction, Long> {
    List<Reaction> findByPost(Post post);
    List<Reaction> findByUser(User user);
    Optional<Reaction> findByUserAndPost(User user, Post post);
}
