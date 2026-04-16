package com.example.casestudy.config;

import com.example.casestudy.model.Article;
import com.example.casestudy.model.Profile;
import com.example.casestudy.model.User;
import com.example.casestudy.repository.ProfileRepository;
import com.example.casestudy.service.PostService;
import com.example.casestudy.service.UserService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Component;

@Component
public class DataInitializer implements CommandLineRunner {

    private static final Logger log = LoggerFactory.getLogger(DataInitializer.class);

    @Autowired
    private UserService userService;

    @Autowired
    private PostService postService;

    @Autowired
    private BCryptPasswordEncoder passwordEncoder;

    @Autowired
    private ProfileRepository profileRepository;

    @Override
    public void run(String... args) throws Exception {
        if (userService.getAllUsers().isEmpty()) {
            initializeUsersAndPosts();
        } else if (postService.getAllPosts().isEmpty()) {
            initializePostsOnly();
        }
    }

    private void initializeUsersAndPosts() {
        User admin   = new User("admin",   "admin@miniblog.com",   passwordEncoder.encode("admin123"));
        admin.setRole("ADMIN");
        User slender = new User("slender", "slender@example.com", passwordEncoder.encode("slender123"));
        User test2   = new User("test2",   "test2@example.com",   passwordEncoder.encode("test2123"));

        admin   = userService.createUser(admin);
        slender = userService.createUser(slender);
        test2   = userService.createUser(test2);

        profileRepository.save(new Profile("Site administrator.", null, admin));
        profileRepository.save(new Profile("Loves Spring Boot and coffee.", null, slender));
        profileRepository.save(new Profile("Database enthusiast.", null, test2));

        seedPosts(admin, slender, test2);
        log.info("Dummy data initialized: 3 users and 5 posts");
    }

    private void initializePostsOnly() {
        User admin   = userService.getUserByUsername("admin");
        User slender = userService.getUserByUsername("slender");
        User test2   = userService.getUserByUsername("test2");
        seedPosts(admin, slender, test2);
        log.info("Dummy posts re-seeded for existing users");
    }

    private void seedPosts(User admin, User slender, User test2) {
        postService.addPost(new Article("Hello and welcome to MiniBlog! This is a place to share thoughts, ideas, and interesting articles.", admin));
        postService.addPost(new Article("Spring Boot makes it easy to create stand-alone, production-grade applications. This framework takes an opinionated view of the platform and third-party libraries.", slender));
        postService.addPost(new Article("When designing a database schema, it's important to consider normalization, indexing strategies, and relationships between entities.", test2));
        postService.addPost(new Article("The web development landscape continues to evolve rapidly. Serverless architectures, edge computing, and AI-driven UIs are reshaping what's possible.", slender));
        postService.addPost(new Article("REST uses standard HTTP methods and status codes to build scalable, predictable web services that are easy to consume from any client.", admin));
    }
}
