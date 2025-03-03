# Contributing to Couples Therapy AI Assistant

Thank you for your interest in improving this project! This document will guide you through the contribution process.

## Getting Started

1. **Fork the Repository**
   - Click the "Fork" button at the top right of the repository page
   - Clone your fork locally:
     ```bash
     git clone https://github.com/your-username/couples-therapy-llm.git
     cd couples-therapy-llm
     ```

2. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Your Changes**
   - Follow the coding style of the project
   - Add or update tests as needed
   - Update documentation to reflect your changes

4. **Test Your Changes**
   - Run the application locally
   - Test all features affected by your changes
   - Ensure no existing functionality is broken

5. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "Description of your changes"
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**
   - Go to the repository on GitHub
   - Click "New Pull Request"
   - Select your branch and describe your changes
   - Submit the pull request

## Development Setup

1. **Install Dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   - Copy `.env.example` to `.env`
   - Add your OpenAI API key
   - Configure other settings as needed

3. **Run the Application**
   ```bash
   python start.py
   ```

## Areas for Improvement

Here are some areas where contributions would be particularly welcome:

1. **Frontend Enhancements**
   - Improved UI/UX design
   - Additional features in the interface
   - Better mobile responsiveness

2. **Backend Features**
   - Enhanced error handling
   - Better conversation management
   - Additional API endpoints

3. **Security Improvements**
   - Authentication system
   - Data encryption
   - Rate limiting

4. **Documentation**
   - Better code comments
   - API documentation
   - Usage examples

## Code Style Guidelines

1. **Python**
   - Follow PEP 8 guidelines
   - Use meaningful variable names
   - Add docstrings for functions and classes

2. **HTML/CSS/JavaScript**
   - Use consistent indentation
   - Follow modern ES6+ practices
   - Comment complex logic

## Testing

- Add tests for new features
- Ensure existing tests pass
- Test edge cases and error conditions

## Questions?

Feel free to:
- Open an issue for questions
- Join discussions
- Ask for clarification in pull requests

Thank you for contributing! 