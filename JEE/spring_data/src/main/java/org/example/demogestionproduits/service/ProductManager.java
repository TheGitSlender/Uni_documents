package org.example.demogestionproduits.service;

import org.example.demogestionproduits.dtos.ProductDto;
import org.example.demogestionproduits.dtos.ProductDtoInput;

import java.util.List;

public interface ProductManager {

    ProductDto addProduct(ProductDtoInput productDtoInput);
    List<ProductDto> getAllProducts();
    ProductDto getProductById(Long id);
    List<ProductDto> getProductByName(String name);
    ProductDto updateProduct(Long id, ProductDtoInput productDtoInput);
    void deleteProduct(Long id);
    //Requete pers
    List<ProductDto> getProductsCheaperThan(double price);
}
