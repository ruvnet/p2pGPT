#!/bin/bash

# Introduction to P2PGPT and explanation
echo "Welcome to the P2PGPT installation script!"
echo ""
echo "P2PGPT is an add-on for AutoGPT that enables it to run in a P2P network"
echo "using websockets. AutoGPT is an experimental open-source application"
echo "showcasing the capabilities of the GPT-4 language model."
echo ""
echo "This program, driven by GPT-4, chains together LLM 'thoughts' to"
echo "autonomously achieve whatever goal you set. As one of the first examples"
echo "of GPT-4 running fully autonomously, AutoGPT pushes the boundaries of"
echo "what is possible with AI."
echo ""

# Display the menu
echo "Please choose an option:"
echo "  1) Install AutoGPT"
echo "  2) Uninstall AutoGPT"
echo "  3) Update AutoGPT"
echo "  4) Exit"
read -p "Enter your choice (1-4): " choice

# Define a function to install AutoGPT
install_autogpt() {
  # Check if Git is installed
  if ! command -v git &> /dev/null; then
      echo "Error: Git is not installed. Please install Git and try again."
      exit 1
  fi

  # Check if pip is installed
  if ! command -v pip &> /dev/null; then
      echo "Error: pip is not installed. Please install pip and try again."
      exit 1
  fi

  # Clone the AutoGPT repository into a subdirectory named "Auto-GPT"
  echo "Cloning the AutoGPT repository..."
  if ! git clone https://github.com/Significant-Gravitas/Auto-GPT.git Auto-GPT; then
      echo "Error: Failed to clone the AutoGPT repository."
      exit 1
  fi

  # Navigate to the cloned repository
  cd Auto-GPT || { echo "Error: Failed to enter the Auto-GPT directory."; exit 1; }

  # Install the required dependencies
  echo "Installing dependencies..."
  if ! pip install -r requirements.txt; then
      echo "Error: Failed to install dependencies."
      exit 1
  fi

  echo "AutoGPT installation completed successfully."
}

# Define a function to uninstall AutoGPT
uninstall_autogpt() {
  echo "Uninstalling AutoGPT..."

  # Prompt the user for confirmation before proceeding with the uninstallation
  read -p "Are you sure you want to uninstall AutoGPT? (Yes/No): " response
  if [[ ! "$response" =~ ^[Yy]|[Yy][Ee][Ss]$ ]]; then
    echo "Uninstallation canceled."
    return
  fi

  # Check if the Auto-GPT directory exists
  if [ -d "Auto-GPT" ]; then
    # Remove the Auto-GPT directory and its contents
    rm -rf Auto-GPT
    echo "AutoGPT directory removed successfully."
  else
    echo "AutoGPT directory not found. Nothing to uninstall."
  fi

  # Optionally, you can also uninstall any dependencies that were installed
  # for AutoGPT. However, be cautious as these dependencies may be used by
  # other projects on the system.

  echo "AutoGPT uninstalled successfully."
}


# Define a function to update AutoGPT
update_autogpt() {
  echo "Updating AutoGPT..."

  # Navigate to the Auto-GPT directory
  cd Auto-GPT || { echo "Error: Failed to enter the Auto-GPT directory."; exit 1; }

  # Fetch the latest changes from the remote repository
  git fetch

  # Check if the local branch is behind the remote branch
  if git status -uno | grep -q 'Your branch is behind'; then
    # If the local branch is behind, pull the latest changes
    echo "New version found. Updating..."
    if git pull; then
      # Install the updated dependencies
      if ! pip install -r requirements.txt; then
        echo "Error: Failed to install updated dependencies."
        exit 1
      fi
      echo "AutoGPT updated successfully."
    else
      echo "Error: Failed to update AutoGPT."
      exit 1
    fi
  else
    # If the local branch is up to date, no update is needed
    echo "AutoGPT is already up to date."
  fi
}


# Execute the chosen option
case $choice in
  1) install_autogpt ;;
  2) uninstall_autogpt ;;
  3) update_autogpt ;;
  4) echo "Exiting..." ;;
  *) echo "Invalid choice. Exiting..." ;;
esac
