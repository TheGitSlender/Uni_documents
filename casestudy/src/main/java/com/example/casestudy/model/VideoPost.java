package com.example.casestudy.model;

import jakarta.persistence.*;

@Entity
@DiscriminatorValue("VIDEO")
public class VideoPost extends Post {

    @Column
    private String url;

    public VideoPost() {}

    public VideoPost(String url) {
        this.url = url;
    }

    public VideoPost(String url, User author) {
        this.url = url;
        setAuthor(author);
    }

    @Override
    public String getUrl() { return url; }
    public void setUrl(String url) { this.url = url; }

    @Override
    public String getPreview() { return url; }
}
