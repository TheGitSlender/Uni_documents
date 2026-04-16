package com.example.casestudy.model;

import jakarta.persistence.*;

@Entity
@DiscriminatorValue("ARTICLE")
public class Article extends Post {

    @Column(columnDefinition = "TEXT")
    private String content;

    public Article() {}

    public Article(String content) {
        this.content = content;
    }

    public Article(String content, User author) {
        this.content = content;
        setAuthor(author);
    }

    @Override
    public String getContent() { return content; }
    public void setContent(String content) { this.content = content; }

    @Override
    public String getPreview() { return content; }
}
