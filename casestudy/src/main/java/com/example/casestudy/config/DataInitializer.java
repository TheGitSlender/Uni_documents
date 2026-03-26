package com.example.casestudy.config;

import com.example.casestudy.model.Post;
import com.example.casestudy.model.Profile;
import com.example.casestudy.model.User;
import com.example.casestudy.repository.ProfileRepository;
import com.example.casestudy.service.UserService;
import com.example.casestudy.service.PostManager;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Component;

@Component
public class DataInitializer implements CommandLineRunner {

    private final UserService userService;
    private final PostManager postManager;
    private final BCryptPasswordEncoder passwordEncoder;
    private final ProfileRepository profileRepository;

    public DataInitializer(UserService userService, PostManager postManager, BCryptPasswordEncoder passwordEncoder, ProfileRepository profileRepository) {
        this.userService = userService;
        this.postManager = postManager;
        this.passwordEncoder = passwordEncoder;
        this.profileRepository = profileRepository;
    }

    @Override
    public void run(String... args) throws Exception {
        if (userService.getAllUsers().isEmpty()) {
            initializeData();
        }
    }

    private void initializeData() {
        User admin = new User("admin", "admin@miniblog.com", passwordEncoder.encode("admin123"));
        admin.setRole("ADMIN");
        User alice = new User("alice", "alice@example.com", passwordEncoder.encode("alice123"));
        User bob   = new User("bob",   "bob@example.com",   passwordEncoder.encode("bob123"));

        admin = userService.createUser(admin);
        alice = userService.createUser(alice);
        bob   = userService.createUser(bob);

        profileRepository.save(new Profile("Site administrator.", null, admin));
        profileRepository.save(new Profile("Loves Spring Boot and coffee.", null, alice));
        profileRepository.save(new Profile("Database enthusiast.", null, bob));

        postManager.addPost(new Post("Hello and welcome to MiniBlog! This is a place to share thoughts, ideas, and interesting articles.", admin));
        postManager.addPost(new Post("Spring Boot makes it easy to create stand-alone, production-grade applications. This framework takes an opinionated view of the platform and third-party libraries.", alice));
        postManager.addPost(new Post("When designing a database schema, it's important to consider normalization, indexing strategies, and relationships between entities.", bob));
        postManager.addPost(new Post("The web development landscape continues to evolve rapidly. Serverless architectures, edge computing, and AI-driven UIs are reshaping what's possible.", alice));
        postManager.addPost(new Post("REST uses standard HTTP methods and status codes to build scalable, predictable web services that are easy to consume from any client.", admin));

        System.out.println("Dummy data initialized: 3 users and 5 posts");
    }
}
