package main

import (
	"context"
	"fmt"
	"log"
	"net"

	pb "github.com/danielsmith/utilities/grpc/proto"
	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
)

// 1. Implement the service logic
type userLookupServer struct {
	pb.UnimplementedUserLookupServer
}

func (s *userLookupServer) GetUser(ctx context.Context, req *pb.UserRequest) (*pb.UserResponse, error) {
	log.Printf("Server received request for User ID: %d", req.Id)

	// Mock database lookup
	if req.Id == 1 {
		// Return the Protobuf message object
		return &pb.UserResponse{
			Id:       1,
			Username: "john_doe",
			Email:    "john_doe@example.com",
			IsActive: true,
		}, nil
	}

	// Handling errors in gRPC
	return nil, status.Error(codes.NotFound, "User not found")
}

// 2. Boilerplate to start the server
func main() {
	// Create a TCP listener on port 50051
	lis, err := net.Listen("tcp", ":50051")
	if err != nil {
		log.Fatalf("Failed to listen: %v", err)
	}

	// Create a new gRPC server
	grpcServer := grpc.NewServer()

	// Register our service implementation
	pb.RegisterUserLookupServer(grpcServer, &userLookupServer{})

	fmt.Println("Starting gRPC server on port 50051...")
	fmt.Println("gRPC server is running on port 50051...")

	// Start serving
	if err := grpcServer.Serve(lis); err != nil {
		log.Fatalf("Failed to serve: %v", err)
	}
}
