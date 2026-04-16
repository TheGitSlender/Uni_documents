package com.example.casestudy.repository;

import com.example.casestudy.model.Post;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface PostRepository extends JpaRepository<Post, Long> {

    @Query("SELECT p FROM Post p WHERE " +
           "(SELECT COUNT(DISTINCT t) FROM p.tags t WHERE t.name IN :tagNames) = :tagCount")
    List<Post> findByAllTagNames(@Param("tagNames") List<String> tagNames,
                                 @Param("tagCount") long tagCount);
}
