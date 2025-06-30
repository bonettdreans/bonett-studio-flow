import cv2
import numpy as np
from typing import Tuple


class GreenScreenService:

    @staticmethod
    def remove_green_screen(
        image_path: str,
        lower_bound: Tuple[int, int, int] = (40, 100, 20),
        upper_bound: Tuple[int, int, int] = (80, 255, 255)
    ) -> np.ndarray:
        """
        Remove fundo verde criando transparência

        Args:
            image_path: Caminho da imagem
            lower_bound: Limite inferior para detecção de verde (HSV)
            upper_bound: Limite superior para detecção de verde (HSV)

        Returns:
            Imagem numpy array com canal alpha
        """
        image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

        if image is None:
            raise FileNotFoundError(
                f"Não foi possível carregar a imagem: {image_path}")

        if len(image.shape) == 3 and image.shape[2] == 4:
            return image

        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        mask = cv2.inRange(hsv, lower_bound, upper_bound)

        inverted_mask = cv2.bitwise_not(mask)

        transparent_image = np.zeros(
            (image.shape[0], image.shape[1], 4), dtype=np.uint8
        )

        transparent_image[:, :, :3] = image

        transparent_image[:, :, 3] = inverted_mask

        return transparent_image

    @staticmethod
    def save_transparent_image(image: np.ndarray, output_path: str) -> None:
        """
        Salva imagem com transparência em formato PNG

        Args:
            image: Imagem numpy array com canal alpha
            output_path: Caminho para salvar a imagem
        """
        if len(image.shape) != 3 or image.shape[2] != 4:
            raise ValueError("A imagem deve ter 4 canais (BGRA)")

        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGBA)
        cv2.imwrite(output_path, rgb_image)

    @staticmethod
    def adjust_green_detection(
        image_path: str,
        hue_range: int = 20,
        saturation_min: int = 100,
        value_min: int = 20
    ) -> np.ndarray:
        """
        Versão mais flexível para ajustar a detecção de verde

        Args:
            image_path: Caminho da imagem
            hue_range: Variação de matiz para verde (padrão: 20)
            saturation_min: Saturação mínima (padrão: 100)
            value_min: Valor mínimo (padrão: 20)

        Returns:
            Imagem numpy array com canal alpha
        """
        # Verde no HSV está aproximadamente em 60 (matiz)
        green_hue = 60
        lower_bound = (green_hue - hue_range, saturation_min, value_min)
        upper_bound = (green_hue + hue_range, 255, 255)

        return GreenScreenService.remove_green_screen(
            image_path, lower_bound, upper_bound
        )
