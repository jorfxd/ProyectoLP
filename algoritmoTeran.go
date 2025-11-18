package main

import "fmt"

func main() {
    var x int = 10
    y := 20
    // Operadores bit a bit:
    z := (x | y) ^ (y &^ x)
    z <<= 1
    if x < y {
        fmt.Println("hola", x+y, z)
    } else {
        fmt.Println(`chao`)
    }
}
