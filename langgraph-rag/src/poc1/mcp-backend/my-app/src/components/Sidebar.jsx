import { Box, IconButton, Avatar } from "@mui/material";
import { motion } from "framer-motion";
import AutoAwesomeIcon from "@mui/icons-material/AutoAwesome";
import EditIcon from "@mui/icons-material/Edit";
import SearchIcon from "@mui/icons-material/Search";
import ImageIcon from "@mui/icons-material/Image";

const MotionIcon = motion(IconButton);

export default function Sidebar() {
  return (
    <Box
      width="70px"
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="space-between"
      py={3}
      sx={{
        bgcolor: "#fff",
        position: "fixed",
        top: 0,
        bottom: 0,
        left: 0,
      }}
    >
      {/* TOP ICONS */}
      <Box display="flex" flexDirection="column" alignItems="center" gap={3}>
        <MotionIcon
          whileHover={{ scale: 1.15 }}
          sx={{ color: "#111" }}
        >
          <AutoAwesomeIcon fontSize="medium" />
        </MotionIcon>

        <MotionIcon whileHover={{ scale: 1.15 }} sx={{ color: "#111" }}>
          <EditIcon />
        </MotionIcon>

        <MotionIcon whileHover={{ scale: 1.15 }} sx={{ color: "#111" }}>
          <SearchIcon />
        </MotionIcon>

        <MotionIcon whileHover={{ scale: 1.15 }} sx={{ color: "#111" }}>
          <ImageIcon />
        </MotionIcon>
      </Box>

      {/* BOTTOM PROFILE ICON */}
      <MotionIcon whileHover={{ scale: 1.15 }}>
        <Avatar
          src="/your-profile-img.jpg"
          sx={{ width: 40, height: 40 }}
        />
      </MotionIcon>
    </Box>
  );
}
