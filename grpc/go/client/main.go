package main

import (
	"context"
	"fmt"
	"log"
	"time"

	pb "github.com/danielsmith/utilities/grpc/proto"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

func main() {
	// 1. Open a channel to the server
	conn, err := grpc.NewClient("localhost:50051", grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		log.Fatalf("Failed to connect: %v", err)
	}
	defer conn.Close()

	// 2. Create a stub (client)
	client := pb.NewUserLookupClient(conn)

	// 3. Create a valid request message
	requestPayload := &pb.UserRequest{Id: 1}

	fmt.Printf("Client sending request for User ID: %d\n", requestPayload.Id)

	// 4. Make the call with timeout
	ctx, cancel := context.WithTimeout(context.Background(), time.Second)
	defer cancel()

	response, err := client.GetUser(ctx, requestPayload)
	if err != nil {
		log.Fatalf("gRPC Error: %v", err)
	}

	// 5. Process the response
	fmt.Println("Client received response:")
	fmt.Printf("User ID: %d\n", response.Id)
	fmt.Printf("Username: %s\n", response.Username)
	fmt.Printf("Email: %s\n", response.Email)
	fmt.Printf("Is Active: %t\n", response.IsActive)
}
