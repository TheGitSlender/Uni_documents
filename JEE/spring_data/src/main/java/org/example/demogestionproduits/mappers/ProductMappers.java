package org.example.demogestionproduits.mappers;

import org.example.demogestionproduits.dao.entities.Product;
import org.example.demogestionproduits.dtos.ProductDto;
import org.example.demogestionproduits.dtos.ProductDtoInput;
import org.modelmapper.ModelMapper;
import org.springframework.stereotype.Component;

@Component
public class ProductMappers {

    private ModelMapper modelMapper = new ModelMapper();

    public Product fromProuduitDtoToProduct(ProductDto ProductDto) {
        return this.modelMapper.map(ProductDto, Product.class);
    }

    public ProductDto fromProuduitToProductDto(Product Product) {
        return this.modelMapper.map(Product, ProductDto.class);
    }

    public ProductDto fromProuduitDtoInputToProductDto(ProductDtoInput ProductDtoInput) {
        return this.modelMapper.map(ProductDtoInput, ProductDto.class);
    }

    public ProductDtoInput fromProuduitDtoToProductDtoInput(ProductDto ProductDTo) {
        return this.modelMapper.map(ProductDTo, ProductDtoInput.class);
    }

    public Product fromProuduitDtoInputToProduct(ProductDtoInput ProductDtoInput) {
        return this.modelMapper.map(ProductDtoInput, Product.class);
    }

}
