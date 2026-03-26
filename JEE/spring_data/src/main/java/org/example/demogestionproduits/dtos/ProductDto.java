package org.example.demogestionproduits.dtos;

import lombok.*;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
@ToString
public class ProductDto {
    private Long id;
    private String name;
    private Long price ;

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }



    public Long getPrice() {
        return price;
    }

    public void setPrice(Long price) {
        this.price = price;
    }



    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }


}
