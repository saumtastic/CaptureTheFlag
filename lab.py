import heapq
from collections import defaultdict, namedtuple


# Node structure for the Huffman Tree (leaf nodes)
class Node(namedtuple("Node", ["char", "freq"])):
    def __lt__(self, other):
        return self.freq < other.freq


# Internal node for merged nodes in the tree
class InternalNode(namedtuple("InternalNode", ["left", "right", "freq"])):
    def __lt__(self, other):
        return self.freq < other.freq


# Build the Huffman Tree
def build_huffman_tree(frequency):
    # Create a priority queue (min-heap) from the frequency dictionary
    heap = [Node(char, freq) for char, freq in frequency.items()]
    heapq.heapify(heap)

    # Combine nodes until only one remains (the root of the Huffman tree)
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = InternalNode(left, right, left.freq + right.freq)
        heapq.heappush(heap, merged)

    # Return the root of the Huffman tree (should be the only node left)
    return heapq.heappop(heap)


# Generate Huffman codes by traversing the tree
def generate_huffman_codes(node, prefix="", huffman_code=None):
    if huffman_code is None:
        huffman_code = {}

    if isinstance(node, Node):
        # Leaf node: assign the prefix as the code for this character
        huffman_code[node.char] = prefix
    else:
        # Internal node: traverse left and right
        generate_huffman_codes(node.left, prefix + "0", huffman_code)
        generate_huffman_codes(node.right, prefix + "1", huffman_code)

    return huffman_code


# Compress the input text using Huffman coding
def huffman_compress(text):
    # Step 1: Calculate frequency of each character in the input text
    frequency = defaultdict(int)
    for char in text:
        frequency[char] += 1

    # Step 2: Build the Huffman tree based on character frequencies
    huffman_tree = build_huffman_tree(frequency)

    # Step 3: Generate Huffman codes for each character by traversing the tree
    huffman_code = generate_huffman_codes(huffman_tree)

    # Step 4: Encode the input text using the generated Huffman codes
    encoded_text = ''.join(huffman_code[char] for char in text)

    return encoded_text, huffman_code, huffman_tree


# Huffman decoding function
def HuffmanDecoding(encodedData, huffmanTree):
    treeHead = huffmanTree
    decodedOutput = []

    # Traverse encoded data to decode it using the Huffman tree
    for x in encodedData:
        if x == '1':
            huffmanTree = huffmanTree.right
        elif x == '0':
            huffmanTree = huffmanTree.left

            # Check if we reached a leaf node (has a character)
        if isinstance(huffmanTree, Node):
            # Append the character to the output and reset to root
            decodedOutput.append(huffmanTree.char)
            huffmanTree = treeHead

            # Join the decoded characters into the final string
    string = ''.join([str(item) for item in decodedOutput])
    return string


# Example usage
if __name__ == "__main__":
    text = "hello huffman"
    print("Original Text:", text)

    # Compress the text using Huffman coding
    compressed_text, huffman_code, huffman_tree = huffman_compress(text)
    print("\nHuffman Encoded Text:", compressed_text)
    print("Huffman Codes:", huffman_code)

    # Decompress the encoded text using the provided HuffmanDecoding function
    decompressed_text = HuffmanDecoding(compressed_text, huffman_tree)
    print("\nDecompressed Text:", decompressed_text)
