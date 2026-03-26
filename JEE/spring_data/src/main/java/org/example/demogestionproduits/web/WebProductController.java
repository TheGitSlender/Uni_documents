package org.example.demogestionproduits.web;

import lombok.RequiredArgsConstructor;
import org.example.demogestionproduits.dtos.ProductDto;
import org.example.demogestionproduits.dtos.ProductDtoInput;
import org.example.demogestionproduits.service.ProductManager;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@Controller
@RequestMapping("/products")
@RequiredArgsConstructor
public class WebProductController {

    @Autowired
    private ProductManager productManager;

    // Liste des produits
    @GetMapping
    public String listProducts(Model model) {
        List<ProductDto> products = productManager.getAllProducts();
        model.addAttribute("products", products);
        return "products/list";
    }

    // Formulaire ajout produit
    @GetMapping("/add")
    public String showAddForm(Model model) {
        model.addAttribute("product", new ProductDtoInput());
        return "products/add";
    }

    // POST ajout produit
    @PostMapping("/add")
    public String addProduct(@ModelAttribute ProductDtoInput productDtoInput) {
        productManager.addProduct(productDtoInput);
        return "redirect:/products";
    }

    // Formulaire modification
    @GetMapping("/edit/{id}")
    public String showEditForm(@PathVariable Long id, Model model) {
        ProductDto product = productManager.getProductById(id);

        ProductDtoInput input = new ProductDtoInput();
        input.setName(product.getName());
        input.setPrice(product.getPrice());

        model.addAttribute("product", input);
        model.addAttribute("id", id);   // <--- id passé séparément pour le formulaire
        return "products/edit";
    }

    // POST modification
    @PostMapping("/edit/{id}")
    public String editProduct(@PathVariable Long id, @ModelAttribute ProductDtoInput productDtoInput) {
        productManager.updateProduct(id, productDtoInput);
        return "redirect:/products";
    }

    // DELETE produit
    @GetMapping("/delete/{id}")
    public String deleteProduct(@PathVariable Long id) {
        productManager.deleteProduct(id);
        return "redirect:/products";
    }

    // Filtrer par prix
    @GetMapping("/filter")
    public String filterByPrice(@RequestParam double price, Model model) {
        List<ProductDto> products = productManager.getProductsCheaperThan(price);
        model.addAttribute("products", products);
        return "products/list";
    }
}
