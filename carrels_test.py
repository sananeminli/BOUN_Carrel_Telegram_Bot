from unittest.mock import AsyncMock

import carrels


async def test_show_carrel_location():
    """Test carrels.show_carrel_location function"""
    # Arrange
    update = AsyncMock()

    # Act
    await carrels.show_carrel_location(update, None)

    # Assert
    assert update.message.reply_photo.call_count == 2


async def test_show_empty(mocker):
    """Test carrels.show_empty function"""
    # Arrange
    mocker.patch("carrels.get_empty_carrels", return_value="Hepsi Dolu!")
    mocker.patch("carrels.logger")
    update = AsyncMock()

    # Act
    await carrels.show_empty(update, None)

    # Assert
    assert update.message.reply_text.called_once
    assert not carrels.logger.warning.called


async def test_show_empty_with_warning(mocker):
    """Test carrels.show_empty function"""
    # Arrange
    mocker.patch("carrels.get_empty_carrels", return_value=None)
    mocker.patch("carrels.logger")
    update = AsyncMock()

    # Act
    await carrels.show_empty(update, None)

    # Assert
    assert not update.message.reply_text.called
    assert carrels.logger.warning.called


async def test_help():
    """Test carrels.help function"""
    # Arrange
    update = AsyncMock()

    # Act
    await carrels.help(update, None)

    # Assert
    assert update.message.reply_text.called_once


def test_main(mocker):
    """Test carrels.main function"""
    # Arrange
    mocker.patch("carrels.Update")
    mocker.patch("carrels.CommandHandler")
    mocker.patch("carrels.Application")

    # Act
    carrels.main()

    # Assert
    assert carrels.Update.called_once
    assert carrels.CommandHandler.call_count == 5
