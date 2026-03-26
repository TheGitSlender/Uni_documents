package com.example.casestudy.model;

import jakarta.persistence.*;

@Entity
public class Profile {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(columnDefinition = "TEXT")
    private String bio;

    private String avatar;

    @OneToOne
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    public Profile() {}

    public Profile(String bio, String avatar, User user) {
        this.bio = bio;
        this.avatar = avatar;
        this.user = user;
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getBio() { return bio; }
    public void setBio(String bio) { this.bio = bio; }

    public String getAvatar() { return avatar; }
    public void setAvatar(String avatar) { this.avatar = avatar; }

    public User getUser() { return user; }
    public void setUser(User user) { this.user = user; }
}
