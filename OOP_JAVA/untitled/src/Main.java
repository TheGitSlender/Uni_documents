
public class Main {
    static int[] table_sort(int[] table) {
        for (int i = 0; i < table.length - 1; i++) {
            for (int j = i + 1; j < table.length; j++) {
                if (table[i] > table[j]) {
                    int temp = table[i];
                    table[i] = table[j];
                    table[j] = temp;
                }
            }
        }
        return table;
    }
    static int[][] table_sort2(int[] table) {
        int[] negative = new int[table.length-1];
        int neg_index = 0;
        int[] positive = new int[table.length-1];
        int pos_index = 0;
        for (int i = 0; i < table.length; i++) {
            int min_index = i;
            for (int j = i; j < table.length; j++) {
                if (table[min_index] > table[j]) {
                    min_index = j;
                }
            }
            int min = table[min_index];
            table[min_index] = table[i];
            table[i] = min;
            if (table[i]<0) {
                negative[neg_index] = table[i];
                neg_index++;
            } else {
                positive[pos_index] = table[i];
                pos_index++;
            }
        }
        int[][] result = new int[2][];
        result [0] = java.util.Arrays.copyOf(negative,neg_index);
        result [1] = java.util.Arrays.copyOf(positive,pos_index);
        return result;
    }

    public static void main(String[] args) {
        int[] table = {3, -1, 4, -5, 2};
        int[][] sortedTables = table_sort2(table);

        System.out.println("Negative numbers:");
        for (int i : sortedTables[0]) {
            System.out.print(i + " ");
        }
        System.out.println("\nPositive numbers:");
        for (int i : sortedTables[1]) {
            System.out.print(i + " ");
        }
    }
}