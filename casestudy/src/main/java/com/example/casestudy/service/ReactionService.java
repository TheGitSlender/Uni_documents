package com.example.casestudy.service;

import com.example.casestudy.model.Post;
import com.example.casestudy.model.Reaction;
import com.example.casestudy.model.ReactionType;
import com.example.casestudy.model.User;
import com.example.casestudy.repository.ReactionRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Optional;

@Service
public class ReactionService {

    @Autowired
    private ReactionRepository reactionRepository;

    @Transactional
    public void react(Post post, User user, ReactionType type) {
        Optional<Reaction> existing = reactionRepository.findByUserAndPost(user, post);
        if (existing.isPresent()) {
            Reaction r = existing.get();
            if (r.getType() == type) {
                reactionRepository.delete(r);
            } else {
                r.setType(type);
                reactionRepository.save(r);
            }
        } else {
            reactionRepository.save(new Reaction(type, user, post));
        }
    }

    public Map<String, Long> getReactionCounts(Post post) {
        Map<String, Long> counts = new LinkedHashMap<>();
        for (ReactionType t : ReactionType.values()) {
            counts.put(t.name(), 0L);
        }
        reactionRepository.findByPost(post).forEach(r -> counts.merge(r.getType().name(), 1L, Long::sum));
        return counts;
    }

    public Optional<ReactionType> getUserReactionType(Post post, User user) {
        return reactionRepository.findByUserAndPost(user, post).map(Reaction::getType);
    }
}
