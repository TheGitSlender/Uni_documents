package org.example.demogestionproduits.web;

import lombok.RequiredArgsConstructor;
import org.example.demogestionproduits.dtos.ProductDto;
import org.example.demogestionproduits.dtos.ProductDtoInput;
import org.example.demogestionproduits.service.ProductManager;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/products")
@RequiredArgsConstructor
public class RestProductController {
    @Autowired
    private ProductManager productManager;

    // ADD
    @PostMapping
    public ProductDto addProduct(@RequestBody ProductDtoInput productDtoInput) {
        return productManager.addProduct(productDtoInput);
    }

    // GET ALL
    @GetMapping
    public List<ProductDto> getAllProducts() {
        return productManager.getAllProducts();
    }

    // GET BY ID
    @GetMapping("/{id}")
    public ProductDto getProductById(@PathVariable Long id) {
        return productManager.getProductById(id);
    }

    // GET BY NAME
    @GetMapping("/search")
    public List<ProductDto> getProductByName(@RequestParam String name) {
        return productManager.getProductByName(name);
    }

    // UPDATE
    @PutMapping("/{id}")
    public ProductDto updateProduct(@PathVariable Long id,
                                    @RequestBody ProductDtoInput productDtoInput) {
        return productManager.updateProduct(id, productDtoInput);
    }

    // DELETE
    @DeleteMapping("/{id}")
    public void deleteProduct(@PathVariable Long id) {
        productManager.deleteProduct(id);
    }
    //Req pers
    @GetMapping("/cheaper-than")
    public List<ProductDto> getProductsCheaperThan(@RequestParam double price) {
        return productManager.getProductsCheaperThan(price);
    }
}