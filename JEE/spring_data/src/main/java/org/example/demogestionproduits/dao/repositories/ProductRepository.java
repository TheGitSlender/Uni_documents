package org.example.demogestionproduits.dao.repositories;

import org.example.demogestionproduits.dao.entities.Product;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

//JpaRepository est une interface fournie par Spring Data JPA qui
// contient déjà des méthodes prêtes à l’emploi
//Spring génère automatiquement une classe qui implémente cette
// interface au runtime : Donc tu n’as pas besoin d’écrire la classe.
//@Repository : optionnel
public interface ProductRepository extends JpaRepository<Product, Long>
{
    // Méthode personnalisée (Dérivée (automatique) crée par spring)
    //Spring analyse le nom de la méthode et génère automatiquement la requête SQL :
    List<Product> findByName(String name);

    //requete personnalisée (géréé par spring)
    //Spring analyse le nom de la méthode et génère automatiquement la requête SQL :
    //select * from product where price < = ?
    List<Product> findByPriceLessThan(double price);

    // Requête personnalisée JPQL
    //Product : nom de la classe entité (PAS le nom de la table)
    @Query("SELECT p FROM Product p WHERE p.price < :price")
    List<Product> findProductsCheaperThan(@Param("price") double price);

    //SQL Natif
    @Query(value = "SELECT * FROM product WHERE price < :price", nativeQuery = true)
    List<Product> findProductsCheaperThanNative(@Param("price") double price);
}
