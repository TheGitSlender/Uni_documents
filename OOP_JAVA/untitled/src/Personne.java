public class Personne {
    private String name;
    public Personne(String nom){
        this.name = nom;
    }
    public int compare(Personne p) {
        return name.compareTo(p.name);
    }

    public String getNom(){
        return name;
    }
    public void setNom(String nom){
        this.name = nom;
    }
    public void sePresenter(){
        System.out.println("Je suis une personne et je m'appelle " + this.name);
    }
}

