package main

import (
	"bufio"
	"flag"
	"fmt"
	"net"
	"net/http"
	"net/url"
	"os"
	"strings"
	"sync"
	"time"
)

var (
	inputFile  = flag.String("input", "", "Path to file containing proxies (one per line)")
	outputFile = flag.String("output", "", "Path to file to write good proxies to")
	workers    = flag.Int("workers", 100, "Number of concurrent workers")
	timeout    = flag.Int("timeout", 5000, "Timeout in milliseconds")
)

type ProxyResult struct {
	Proxy   string
	Success bool
	Error   string
}

func checkProxy(proxy string, timeoutMs int) bool {
	// Normalize proxy string (assuming ip:port or protocol://ip:port)
	if !strings.Contains(proxy, "://") {
		proxy = "http://" + proxy
	}

	proxyUrl, err := url.Parse(proxy)
	if err != nil {
		return false
	}

	client := &http.Client{
		Transport: &http.Transport{
			Proxy: http.ProxyURL(proxyUrl),
			DialContext: (&net.Dialer{
				Timeout:   time.Duration(timeoutMs) * time.Millisecond,
				KeepAlive: 30 * time.Second,
			}).DialContext,
			DisableKeepAlives: true, 
		},
		Timeout: time.Duration(timeoutMs) * time.Millisecond,
	}

	// We'll check against a reliable target. Google is good for speed, 
	// but strictly we just need connectivity.
	resp, err := client.Get("http://www.google.com/robots.txt")
	if err != nil {
		return false
	}
	defer resp.Body.Close()

	if resp.StatusCode >= 200 && resp.StatusCode < 300 {
		return true
	}
	return false
}

func worker(id int, jobs <-chan string, results chan<- ProxyResult, wg *sync.WaitGroup) {
	defer wg.Done()
	for proxy := range jobs {
		success := checkProxy(proxy, *timeout)
		results <- ProxyResult{Proxy: proxy, Success: success}
	}
}

func main() {
	flag.Parse()

	if *inputFile == "" {
		fmt.Println("Error: --input argument is required")
		os.Exit(1)
	}

	// Open input file
	file, err := os.Open(*inputFile)
	if err != nil {
		fmt.Printf("Error opening input file: %v\n", err)
		os.Exit(1)
	}
	defer file.Close()

	// Read proxies
	var proxies []string
	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if line != "" {
			proxies = append(proxies, line)
		}
	}

	// Output management
	var out *os.File
	if *outputFile != "" {
		out, err = os.Create(*outputFile)
		if err != nil {
			fmt.Printf("Error creating output file: %v\n", err)
			os.Exit(1)
		}
		defer out.Close()
	} else {
		out = os.Stdout
	}

	// Channels
	jobs := make(chan string, len(proxies))
	results := make(chan ProxyResult, len(proxies))

	// Start workers
	var wg sync.WaitGroup
	for w := 1; w <= *workers; w++ {
		wg.Add(1)
		go worker(w, jobs, results, &wg)
	}

	// Feed workers
	for _, p := range proxies {
		jobs <- p
	}
	close(jobs)

	// Collect results in a separate goroutine to not block
	go func() {
		wg.Wait()
		close(results)
	}()

	// Process results
	goodCount := 0
	for res := range results {
		if res.Success {
			goodCount++
			if *outputFile != "" {
				out.WriteString(res.Proxy + "\n")
			} else {
				fmt.Println(res.Proxy)
			}
		}
	}
}
