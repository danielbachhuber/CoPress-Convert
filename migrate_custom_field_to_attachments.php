<?php
/**
 * migrate_custom_field_to_attachments.php
 */

require_once( 'wp-load.php' );

global $wpdb, $blog_id;
// Get all of the results from the database
$results = $wpdb->get_results( "SELECT * FROM " . $wpdb->postmeta . " WHERE meta_key='migrated_image';" );
echo "\nReturned " . count( $results ) . " results from the database\n\n";

foreach( $results as $key => $result ) {

	// Only convert posts that don't have featured images
	if ( !has_post_thumbnail( $result->post_id ) ) {
		
		$image = explode( '{}', $result->meta_value );
		
		$image_uri = $image[0];
		$image_caption = $image[1];
		$image_credit = $image[2];
		$wp_filetype = wp_check_filetype(basename($image_uri), null );
		$attachment = array(
			'post_mime_type' => $wp_filetype['type'],
			'post_title' => preg_replace('/\.[^.]+$/', '', basename( $image_uri ) ),
			'post_content' => '',
			'post_status' => 'inherit'
			);
		$upload_dir = wp_upload_dir();
		// Filename to insert an attachment must be the absolute path on the server
		$image_uri = $upload_dir['basedir'] . $image_uri;	
		$attach_id = wp_insert_attachment( $attachment, $image_uri, $result->post_id );
		echo "Adding $image_uri as attachment to $result->post_id. Attach #$attach_id\n";
		// you must first include the image.php file
		// for the function wp_generate_attachment_metadata() to work
		require_once(ABSPATH . "wp-admin" . '/includes/image.php');
		// Filename to generate different thumbnail versions needs to have the URL
		$image_uri = str_replace( $upload_dir['basedir'], $upload_dir['baseurl'], $image_uri );
		$attach_data = wp_generate_attachment_metadata( $attach_id, $image_uri );
		wp_update_attachment_metadata( $attach_id,  $attach_data );
		// Set it as a featured image
		update_post_meta( $result->post_id, '_thumbnail_id', $attach_id );
		echo "Added attach #$attach_id as featured image to post $result->post_id\n\n";
	} else {
		echo "Post $result->post_id already has a featured image.\n\n";
	}
	
} // END foreach( $results as $post )

// Get all of the image thumbnails from the database.
// For each thumbnail, add it as an attachment if it isn't already
// Set it as a featured image


?>