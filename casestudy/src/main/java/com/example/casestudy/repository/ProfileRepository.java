package com.example.casestudy.repository;

import com.example.casestudy.model.Profile;
import com.example.casestudy.model.User;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface ProfileRepository extends JpaRepository<Profile, Long> {
    Optional<Profile> findByUser(User user);
}
