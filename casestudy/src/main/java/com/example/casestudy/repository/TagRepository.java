package com.example.casestudy.repository;

import com.example.casestudy.model.Tag;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface TagRepository extends JpaRepository<Tag, Long> {
    Optional<Tag> findByName(String name);

    @Query("SELECT t FROM Tag t WHERE t.posts IS EMPTY")
    List<Tag> findOrphanedTags();
}
