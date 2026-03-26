package org.example.demogestionproduits.service;

import org.example.demogestionproduits.dao.entities.Product;
import org.example.demogestionproduits.dao.repositories.ProductRepository;
import org.example.demogestionproduits.dtos.ProductDto;
import org.example.demogestionproduits.dtos.ProductDtoInput;
import org.example.demogestionproduits.mappers.ProductMappers;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.stream.Collectors;

@Service
public class ProductService implements ProductManager {
    @Autowired
    private ProductRepository productRepository;
    @Autowired
    private ProductMappers productMappers;

    @Override
    public ProductDto addProduct(ProductDtoInput productDtoInput) {
        Product product = productMappers.fromProuduitDtoInputToProduct(productDtoInput);
        Product savedProduct = productRepository.save(product);
        return productMappers.fromProuduitToProductDto(savedProduct);
    }

    @Override
    public List<ProductDto> getAllProducts() {
        return productRepository.findAll()
                .stream()
                .map(productMappers::fromProuduitToProductDto)
                .collect(Collectors.toList());
    }

    @Override
    public ProductDto getProductById(Long id) {
        Product product = productRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Produit non trouvé"));
        return productMappers.fromProuduitToProductDto(product);
    }

    @Override
    public List<ProductDto> getProductByName(String name) {
        return productRepository.findByName(name)
                .stream()
                .map(productMappers::fromProuduitToProductDto)
                .collect(Collectors.toList());
    }

    @Override
    public ProductDto updateProduct(Long id, ProductDtoInput productDtoInput) {
        Product existingProduct = productRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Produit non trouvé"));
        existingProduct.setName(productDtoInput.getName());
        existingProduct.setPrice(productDtoInput.getPrice());
        Product updatedProduct = productRepository.save(existingProduct);
        return productMappers.fromProuduitToProductDto(updatedProduct);
    }

    @Override
    public void deleteProduct(Long id) {
        productRepository.deleteById(id);
    }

    //**********
    @Override
    public List<ProductDto> getProductsCheaperThan(double price) {
        return productRepository.findProductsCheaperThan(price)
                .stream()
                .map(productMappers::fromProuduitToProductDto)
                .toList();
    }
}