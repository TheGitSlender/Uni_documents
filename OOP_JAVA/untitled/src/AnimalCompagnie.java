public interface AnimalCompagnie {
    String get_name();
    void set_name(String new_name);
    void jouer();

    default void message() {
        System.out.println("Je susi un animal de compagnie.");
    }
}
