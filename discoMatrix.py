public class ImprimirMatriz {
    public static void main(String[] args) {
        int[][] matriz = new int[10][10];


        for (int i = 0; i < 10; i++) {
            for (int j = 0; j < 10; j++) {
                matriz[i][j] = i + j; 
            }
        }


        for (int i = 0; i < 10; i++) {
            for (int j = 0; j < 10; j++) {
                // System.out.printf ayuda a que las columnas queden alineadas
                System.out.printf("%4d", matriz[i][j]);
            }
            System.out.println(); // Salto de línea al terminar cada fila
        }
    }
}