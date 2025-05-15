public class test_personne {
    public static void main(String[] args) {
        Personne p = new Personne("John");
        Personne p2 = new Personne("Mark");

        System.out.println("Nom de p1: " + p.getNom());
        System.out.println("Nom de p2: " + p2.getNom());
        p.setNom("John2");
        System.out.println("New Nom de p1: " + p.getNom());
        p.sePresenter();
        p2.sePresenter();
        int comparison = p.compare(p2);
        if (comparison < 0) {
            System.out.println(p.getNom() + " vient avant " + p2.getNom());
        } else if (comparison > 0) {
            System.out.println(p.getNom() + " vient après " + p2.getNom());
        } else {
            System.out.println(p.getNom() + " et " + p2.getNom() + " sont identiques.");
        }
    }
}
