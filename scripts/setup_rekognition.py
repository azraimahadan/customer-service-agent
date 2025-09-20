#!/usr/bin/env python3
"""
Script to help set up Rekognition Custom Labels training
This script provides guidance and helper functions for training
"""

import boto3
import json
import os

def create_training_dataset():
    """Create training dataset for Rekognition Custom Labels"""
    
    print("🎯 Rekognition Custom Labels Setup Guide")
    print("========================================")
    
    print("\n📋 Required Steps:")
    print("1. Collect router images showing different states:")
    print("   - Normal operation (green LEDs)")
    print("   - No service errors")
    print("   - Cable disconnected")
    print("   - Power issues")
    print("   - Different router models")
    
    print("\n2. Label your images:")
    print("   - router_normal")
    print("   - router_no_service")
    print("   - router_cable_issue")
    print("   - router_power_issue")
    print("   - router_model_[specific_model]")
    
    print("\n3. Upload images to S3:")
    print("   - Create folder structure in your S3 bucket")
    print("   - Upload at least 10 images per label")
    print("   - More images = better accuracy")
    
    print("\n4. Create manifest files:")
    print("   - Training manifest (80% of images)")
    print("   - Testing manifest (20% of images)")
    
    print("\n5. Train the model:")
    print("   - Use AWS Console or CLI")
    print("   - Training takes 1-24 hours")
    print("   - Costs ~$1-10 depending on dataset size")
    
    print("\n📝 Sample manifest entry:")
    sample_manifest = {
        "source-ref": "s3://your-bucket/images/router1.jpg",
        "bounding-box": {
            "annotations": [
                {
                    "class_id": 0,
                    "left": 0,
                    "top": 0,
                    "width": 100,
                    "height": 100
                }
            ],
            "image_size": [
                {
                    "width": 640,
                    "height": 480,
                    "depth": 3
                }
            ]
        },
        "bounding-box-metadata": {
            "objects": [
                {
                    "confidence": 1
                }
            ],
            "class-map": {
                "0": "router_no_service"
            },
            "type": "groundtruth/object-detection"
        }
    }
    
    print(json.dumps(sample_manifest, indent=2))
    
    print("\n🚀 Quick Start Commands:")
    print("aws rekognition create-project --project-name unifi-router-detection")
    print("aws rekognition create-project-version \\")
    print("  --project-arn <project-arn> \\")
    print("  --version-name v1 \\")
    print("  --training-data '{\"Assets\":[{\"GroundTruthManifest\":{\"S3Object\":{\"Bucket\":\"your-bucket\",\"Name\":\"training.manifest\"}}}]}' \\")
    print("  --testing-data '{\"Assets\":[{\"GroundTruthManifest\":{\"S3Object\":{\"Bucket\":\"your-bucket\",\"Name\":\"testing.manifest\"}}},\"AutoCreate\":false]}'")

def generate_sample_manifest():
    """Generate sample manifest files for training"""
    
    training_manifest = []
    testing_manifest = []
    
    # Sample entries (replace with your actual S3 paths)
    sample_images = [
        ("router_normal_1.jpg", "router_normal"),
        ("router_normal_2.jpg", "router_normal"),
        ("router_no_service_1.jpg", "router_no_service"),
        ("router_no_service_2.jpg", "router_no_service"),
        ("router_cable_issue_1.jpg", "router_cable_issue"),
    ]
    
    for i, (image_name, label) in enumerate(sample_images):
        manifest_entry = {
            "source-ref": f"s3://your-training-bucket/images/{image_name}",
            "class": label,
            "class-metadata": {
                "confidence": 1,
                "human-annotated": "yes",
                "creation-date": "2024-01-01T00:00:00.000Z"
            }
        }
        
        # 80% for training, 20% for testing
        if i % 5 == 0:
            testing_manifest.append(manifest_entry)
        else:
            training_manifest.append(manifest_entry)
    
    # Save manifest files
    with open('training.manifest', 'w') as f:
        for entry in training_manifest:
            f.write(json.dumps(entry) + '\n')
    
    with open('testing.manifest', 'w') as f:
        for entry in testing_manifest:
            f.write(json.dumps(entry) + '\n')
    
    print("✅ Generated training.manifest and testing.manifest")
    print("📤 Upload these files to your S3 bucket before training")

if __name__ == "__main__":
    create_training_dataset()
    print("\n" + "="*50)
    generate_sample_manifest()