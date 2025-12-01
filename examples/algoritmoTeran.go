package main

import (
	"fmt"
	"time"
)

// Suma dos números y devuelve el resultado
func sumar(a int, b int) int {
	return a + b
}

func main() {
	fmt.Println("Hola, Go está funcionando")

	x, y := 7, 5
	resultado := sumar(x, y)
	fmt.Printf("La suma de %d + %d = %d\n", x, y, resultado)

	fmt.Println("Fecha y hora actual:", time.Now())
}
