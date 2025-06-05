package main

import (
	"bytes"
	"context"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"os/exec"
)

const scriptURL = "https://raw.githubusercontent.com/marcmoiagese/repo-scripts/master/restoreEC2/installrestore.py"

func main() {
	fmt.Println("[+] Iniciant procés: descarregar i executar script Python")

	// 1. Descarregar el script a memòria
	scriptContent, err := downloadScript(scriptURL)
	if err != nil {
		log.Fatalf("[-] Error descarregant el script: %v", err)
	}
	fmt.Println("[+] Script carregat a memòria")

	// 2. Executar el script Python directament des de memòria
	err = runPythonScriptInMemory(scriptContent)
	if err != nil {
		log.Fatalf("[-] Error executant el script: %v", err)
	}

	fmt.Println("[+] Script executat amb èxit")
}

// downloadScript descarrega el contingut del script Python a memòria
func downloadScript(url string) ([]byte, error) {
	resp, err := http.Get(url)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("error HTTP: %d", resp.StatusCode)
	}

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}

	return body, nil
}

// runPythonScriptInMemory executa el script Python des de memòria
func runPythonScriptInMemory(script []byte) error {
	cmd := exec.CommandContext(context.Background(), "python3", "-")

	// Passar el contingut del script via stdin
	cmd.Stdin = bytes.NewReader(script)

	// Mostrar stdout i stderr
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr

	// Executar
	return cmd.Run()
}
