import { useState, useRef, useEffect } from "react";
import {
  Box,
  Flex,
  Input,
  IconButton,
  Text,
  Spinner,
  useColorModeValue,
} from "@chakra-ui/react";
import { motion } from "framer-motion";
import { FiSend } from "react-icons/fi";

const MotionBox = motion(Box);

export default function ChatPage() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef();

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  const fixSpacing = (prev, chunk) => {
    if (!prev) return chunk;
    if (!chunk.startsWith(" ") && !chunk.match(/^[.,!?;:]/)) {
      return prev + " " + chunk;
    }
    return prev + chunk;
  };

  const sendMessage = async () => {
    if (!input.trim()) return;

    setMessages((prev) => [...prev, { role: "user", text: input }]);
    setMessages((prev) => [...prev, { role: "ai", text: "" }]);
    setLoading(true);

    const res = await fetch(
      `http://localhost:8000/joke/stream?topic=${input}`,
      { headers: { Accept: "text/event-stream" } }
    );

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    setInput("");

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk
        .split("\n")
        .filter((line) => line.startsWith("data: "));

      for (const line of lines) {
        const data = line.replace("data: ", "").trim();
        if (data === "[DONE]") {
          setLoading(false);
          return;
        }

        setMessages((prev) => {
          const updated = [...prev];
          updated[updated.length - 1].text = fixSpacing(
            updated[updated.length - 1].text,
            data
          );
          return updated;
        });
      }
    }

    setLoading(false);
  };

  return (
    <Flex direction="column" h="100vh" bg={useColorModeValue("gray.100", "gray.900")}>
      {/* HEADER */}
      <Flex
        p={4}
        fontWeight="bold"
        fontSize="xl"
        justify="center"
        borderBottom="1px solid"
        borderColor={useColorModeValue("gray.300", "gray.700")}
        bg={useColorModeValue("white", "gray.800")}
      >
        💬 AI Chat Assistant
      </Flex>

      {/* CHAT WINDOW */}
      <Flex flex="1" direction="column" overflowY="auto" p={4} gap={4}>
        {messages.map((msg, index) => (
          <MotionBox
            key={index}
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.25 }}
            maxW="75%"
            alignSelf={msg.role === "user" ? "flex-end" : "flex-start"}
            bg={
              msg.role === "user"
                ? "blue.500"
                : useColorModeValue("gray.300", "gray.700")
            }
            color={msg.role === "user" ? "white" : "whiteAlpha.900"}
            p={3}
            borderRadius="lg"
            boxShadow="md"
            _hover={{ transform: "scale(1.02)", transition: "0.2s" }}
          >
            {msg.text}
          </MotionBox>
        ))}
        <div ref={chatEndRef} />
      </Flex>

      {/* INPUT AREA */}
      <Flex
        p={4}
        gap={2}
        borderTop="1px solid"
        borderColor={useColorModeValue("gray.300", "gray.700")}
        bg={useColorModeValue("white", "gray.800")}
      >
        <Input
          placeholder="Ask something..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          bg={useColorModeValue("gray.200", "gray.700")}
        />

        <IconButton
          icon={loading ? <Spinner size="sm" /> : <FiSend />}
          aria-label="Send"
          onClick={sendMessage}
          colorScheme="blue"
          borderRadius="full"
          size="lg"
          isDisabled={loading}
          _hover={{ transform: "scale(1.1)" }}
          as={motion.button}
          whileTap={{ scale: 0.9 }}
        />
      </Flex>
    </Flex>
  );
}
